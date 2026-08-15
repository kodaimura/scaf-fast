import assert from "node:assert/strict";

const origin = process.env.API_ORIGIN ?? "http://api:8000";
const apiUrl = `${origin}/api`;
const mailhogUrl = process.env.MAILHOG_URL ?? "http://mailhog:8025";
const runId = Date.now();
const primaryEmail = `primary-${runId}@example.com`;
const secondaryEmail = `secondary-${runId}@example.com`;
const initialPassword = "Password123!";
const changedPassword = "Changed123!";
const resetPassword = "Reset123!";

const call = async (path, { method = "GET", body, token, cookie } = {}) => {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;
  if (cookie) headers.Cookie = cookie;

  const response = await fetch(`${origin}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let json;
  if (text) {
    try {
      json = JSON.parse(text);
    } catch {
      json = undefined;
    }
  }
  return {
    status: response.status,
    json,
    cookie: response.headers.get("set-cookie")?.split(";", 1)[0],
  };
};

const expectStatus = (response, status, label) => {
  assert.equal(
    response.status,
    status,
    `${label}: expected ${status}, received ${response.status} ${JSON.stringify(response.json)}`,
  );
  return response;
};

const login = async (email, password) => {
  const response = expectStatus(
    await call("/api/auth/login", {
      method: "POST",
      body: { login_id: email, password, remember_me: false },
    }),
    200,
    "login",
  );
  assert.equal(typeof response.json?.access_token, "string");
  assert.ok(response.cookie?.startsWith("refresh_token="));
  return response;
};

const findResetToken = async () => {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    const response = await fetch(`${mailhogUrl}/api/v2/messages?limit=50`);
    assert.equal(response.status, 200);
    const messages = await response.json();
    const message = messages.items?.find((item) =>
      item.To?.some(
        (recipient) =>
          `${recipient.Mailbox}@${recipient.Domain}` === primaryEmail,
      ),
    );
    if (message) {
      const body = message.Content?.Body?.replace(/=\r?\n/g, "").replace(
        /=([0-9A-F]{2})/gi,
        (_, hex) => String.fromCharCode(Number.parseInt(hex, 16)),
      );
      const token = body?.match(/[?&]token=([A-Za-z0-9_-]+)/)?.[1];
      assert.ok(token, "password reset token is missing from the email");
      return token;
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  assert.fail("password reset email was not delivered");
};

const health = expectStatus(await call("/health"), 200, "health");
assert.equal(health.json?.status, "ok");
expectStatus(
  await call("/api/auth/refresh", { method: "POST" }),
  401,
  "refresh without cookie",
);
expectStatus(await call("/api/accounts/me"), 401, "unauthenticated account");

const signupBody = {
  login_id: primaryEmail,
  email: primaryEmail,
  password: initialPassword,
  first_name: "Primary",
  last_name: "Account",
};
const signup = expectStatus(
  await call("/api/auth/signup", { method: "POST", body: signupBody }),
  201,
  "signup",
);
assert.equal(signup.json?.account?.email, primaryEmail);
assert.equal("password" in signup.json.account, false);
assert.equal("password_hash" in signup.json.account, false);
expectStatus(
  await call("/api/auth/signup", { method: "POST", body: signupBody }),
  409,
  "duplicate signup",
);
expectStatus(
  await call("/api/auth/login", {
    method: "POST",
    body: {
      login_id: primaryEmail,
      password: "WrongPassword!",
      remember_me: false,
    },
  }),
  401,
  "invalid login",
);

let session = await login(primaryEmail, initialPassword);
let accessToken = session.json.access_token;
const current = expectStatus(
  await call("/api/accounts/me", { token: accessToken }),
  200,
  "current account",
);
assert.equal(current.json?.account?.email, primaryEmail);

const created = expectStatus(
  await call("/api/accounts", {
    method: "POST",
    token: accessToken,
    body: {
      login_id: secondaryEmail,
      email: secondaryEmail,
      password: "Secondary123!",
      first_name: "Secondary",
      last_name: "Account",
    },
  }),
  201,
  "create account",
);
const secondaryId = created.json?.account?.id;
assert.ok(secondaryId);

const accounts = expectStatus(
  await call("/api/accounts", { token: accessToken }),
  200,
  "list accounts",
);
assert.ok(
  accounts.json?.accounts?.some((account) => account.id === secondaryId),
);
expectStatus(
  await call(`/api/accounts/${secondaryId}`, { token: accessToken }),
  200,
  "get account",
);
expectStatus(
  await call("/api/accounts/999999999", { token: accessToken }),
  404,
  "missing account",
);
const updated = expectStatus(
  await call(`/api/accounts/${secondaryId}`, {
    method: "PUT",
    token: accessToken,
    body: {
      login_id: secondaryEmail,
      email: secondaryEmail,
      password: "Secondary456!",
      first_name: "Updated",
      last_name: "Account",
    },
  }),
  200,
  "update account",
);
assert.equal(updated.json?.account?.first_name, "Updated");
const disabled = expectStatus(
  await call(`/api/accounts/${secondaryId}/disable`, {
    method: "PUT",
    token: accessToken,
  }),
  200,
  "disable account",
);
assert.equal(typeof disabled.json?.account?.disabled_at, "string");
expectStatus(
  await call("/api/auth/login", {
    method: "POST",
    body: {
      login_id: secondaryEmail,
      password: "Secondary456!",
      remember_me: false,
    },
  }),
  401,
  "reject disabled account login",
);
const enabled = expectStatus(
  await call(`/api/accounts/${secondaryId}/enable`, {
    method: "PUT",
    token: accessToken,
  }),
  200,
  "enable account",
);
assert.equal(enabled.json?.account?.disabled_at, null);
await login(secondaryEmail, "Secondary456!");

expectStatus(
  await call("/api/accounts/me/password", {
    method: "PUT",
    token: accessToken,
    body: { old_password: "WrongPassword!", new_password: changedPassword },
  }),
  401,
  "reject incorrect current password",
);
expectStatus(
  await call("/api/accounts/me/password", {
    method: "PUT",
    token: accessToken,
    body: { old_password: initialPassword, new_password: changedPassword },
  }),
  204,
  "change password",
);
expectStatus(
  await call("/api/accounts/me", { token: accessToken }),
  401,
  "revoke old access token",
);
expectStatus(
  await call("/api/auth/login", {
    method: "POST",
    body: {
      login_id: primaryEmail,
      password: initialPassword,
      remember_me: false,
    },
  }),
  401,
  "reject old password",
);

session = await login(primaryEmail, changedPassword);
accessToken = session.json.access_token;
const refreshed = expectStatus(
  await call("/api/auth/refresh", {
    method: "POST",
    cookie: session.cookie,
  }),
  200,
  "refresh access token",
);
assert.equal(typeof refreshed.json?.access_token, "string");

expectStatus(
  await call("/api/auth/forgot-password", {
    method: "POST",
    body: { email: `missing-${runId}@example.com` },
  }),
  204,
  "hide unknown password reset account",
);
expectStatus(
  await call("/api/auth/forgot-password", {
    method: "POST",
    body: { email: primaryEmail },
  }),
  204,
  "request password reset",
);
const resetToken = await findResetToken();
expectStatus(
  await call("/api/auth/reset-password/verify?token=invalid-token"),
  400,
  "reject invalid reset token",
);
expectStatus(
  await call(
    `/api/auth/reset-password/verify?token=${encodeURIComponent(resetToken)}`,
  ),
  204,
  "verify reset token",
);
expectStatus(
  await call("/api/auth/reset-password", {
    method: "POST",
    body: { token: resetToken, new_password: resetPassword },
  }),
  204,
  "reset password",
);
expectStatus(
  await call(
    `/api/auth/reset-password/verify?token=${encodeURIComponent(resetToken)}`,
  ),
  400,
  "reject used reset token",
);
await login(primaryEmail, resetPassword);
expectStatus(
  await call("/api/auth/login", {
    method: "POST",
    body: {
      login_id: primaryEmail,
      password: changedPassword,
      remember_me: false,
    },
  }),
  401,
  "reject pre-reset password",
);
expectStatus(
  await call("/api/auth/refresh", {
    method: "POST",
    cookie: session.cookie,
  }),
  401,
  "revoke refresh token after password reset",
);

const logout = expectStatus(
  await call("/api/auth/logout", {
    method: "POST",
    cookie: session.cookie,
  }),
  204,
  "logout",
);
assert.match(logout.cookie ?? "", /^refresh_token=/);

console.log("API E2E contract passed");
