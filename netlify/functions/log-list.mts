import type { Config, Context } from "@netlify/functions";
import { stores, json } from "../lib/shared.mts";

export default async (_req: Request, context: Context) => {
  const { logs } = stores(context);
  const { blobs } = await logs.list();
  const items = (await Promise.all(blobs.map((b) => logs.get(b.key, { type: "json" })))).filter(Boolean);
  items.sort((a: any, b: any) => String(b.date).localeCompare(String(a.date)) || String(b.created).localeCompare(String(a.created)));
  return json({ logs: items });
};

export const config: Config = { path: "/api/logs", method: "GET" };
