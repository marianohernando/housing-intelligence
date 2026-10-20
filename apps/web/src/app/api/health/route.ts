import { envelope } from "@/lib/envelope";

export function GET(): Response {
  return Response.json(envelope({ status: "ok", service: "hi-web" }));
}
