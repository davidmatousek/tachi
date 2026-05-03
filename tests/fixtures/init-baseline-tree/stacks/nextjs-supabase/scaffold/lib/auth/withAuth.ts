// Auth wrapper — verifies the session before running a Server Action callback.
import type { User } from "@supabase/supabase-js";
import { createServerClient } from "@/lib/supabase/server";

type AuthSuccess<T> = { success: true; data: T };
type AuthFailure = { success: false; error: string };
type AuthResult<T> = AuthSuccess<T> | AuthFailure;

export async function withAuth<T>(
  callback: (user: User) => Promise<T>,
): Promise<AuthResult<T>> {
  const supabase = await createServerClient();
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user) {
    return { success: false, error: "Unauthorized" };
  }

  const data = await callback(user);
  return { success: true, data };
}
