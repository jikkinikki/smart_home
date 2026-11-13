// const BASE_URL = import.meta.env.VITE_API_URL;
const BASE_URL = "http://localhost:8000/";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export async function apiRequest<T>(
  method: HttpMethod,
  endpoint: string,
  data?: unknown
): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    ...(data !== undefined && {
      body: JSON.stringify(data),
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}