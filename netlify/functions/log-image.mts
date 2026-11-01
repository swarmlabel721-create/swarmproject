import type { Config, Context } from "@netlify/functions";
import { stores } from "../lib/shared.mts";

export default async (_req: Request, context: Context) => {
  const id = context.params.id;
  const { images } = stores(context);
  const res = await images.getWithMetadata(id, { type: "arrayBuffer" });
  if (!res) return new Response("not found", { status: 404 });
  return new Response(res.data, {
    headers: {
      "content-type": String(res.metadata?.contentType || "image/jpeg"),
      "cache-control": "public, max-age=31536000, immutable",
    },
  });
};

export const config: Config = { path: "/api/log-image/:id", method: "GET" };
