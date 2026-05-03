/**
 * Typed fetch wrapper for the backend API.
 *
 * Reads the API base URL from the VITE_API_URL environment variable.
 * Provides generic request methods with typed responses and structured
 * error handling via the ApiError class.
 *
 * Usage:
 *   const users = await api.get<User[]>("/users");
 *   const user = await api.post<User>("/users", { name: "Alice" });
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

/**
 * Structured API error with status code and response body.
 */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    public readonly body: unknown,
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

/**
 * Generic request function. All HTTP methods route through this.
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = { ...options.headers };
  if (options.body) {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // sends httpOnly cookies for auth
  });

  if (!response.ok) {
    const text = await response.text();
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
    throw new ApiError(response.status, response.statusText, body);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/**
 * Typed API client with convenience methods for each HTTP verb.
 */
export const api = {
  get: <T>(endpoint: string): Promise<T> =>
    request<T>(endpoint, { method: "GET" }),

  post: <T>(endpoint: string, data?: unknown): Promise<T> =>
    request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data: unknown): Promise<T> =>
    request<T>(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  patch: <T>(endpoint: string, data: unknown): Promise<T> =>
    request<T>(endpoint, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: <T>(endpoint: string): Promise<T> =>
    request<T>(endpoint, { method: "DELETE" }),
};
