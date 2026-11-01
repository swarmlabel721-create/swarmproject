import { getStore } from "@netlify/blobs";
import type { Context } from "@netlify/functions";

// 本番とプレビューでデータを分ける（プレビューで試しても本番に混ざらない）
export function stores(context: Context) {
  const prod = context.deploy?.context === "production";
  const suffix = prod ? "" : "-preview";
  return {
    logs: getStore({ name: "earth-log" + suffix, consistency: "strong" }),
    images: getStore({ name: "earth-log-images" + suffix, consistency: "strong" }),
  };
}

export function checkPassword(given: unknown): boolean {
  const expected = Netlify.env.get("UPLOAD_PASSWORD");
  if (!expected || typeof given !== "string" || given.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < given.length; i++) diff |= given.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

export const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
