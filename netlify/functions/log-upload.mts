import type { Config, Context } from "@netlify/functions";
import { stores, checkPassword, json, sleep } from "../lib/shared.mts";

const MAX_IMAGE = 4 * 1024 * 1024;
const TYPES = ["image/jpeg", "image/png", "image/webp"];
const clip = (v: FormDataEntryValue | null, n: number) => (typeof v === "string" ? v.trim().slice(0, n) : "");

export default async (req: Request, context: Context) => {
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    return json({ error: "送信内容を読み取れませんでした" }, 400);
  }
  if (!Netlify.env.get("UPLOAD_PASSWORD")) return json({ error: "アップロード用パスワードがまだ設定されていません" }, 503);
  if (!checkPassword(form.get("password"))) {
    await sleep(1500);
    return json({ error: "パスワードが違います" }, 401);
  }
  const { logs, images } = stores(context);

  // 削除
  if (form.get("action") === "delete") {
    const id = clip(form.get("id"), 80);
    if (!id) return json({ error: "id がありません" }, 400);
    await logs.delete(id);
    await images.delete(id);
    return json({ ok: true, deleted: id });
  }
  // パスワード確認のみ
  if (form.get("action") === "check") return json({ ok: true });

  const title = clip(form.get("title"), 80);
  const date = clip(form.get("date"), 10);
  const photo = form.get("photo");
  if (!title) return json({ error: "タイトルを入れてください" }, 400);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return json({ error: "日付が不正です" }, 400);
  if (!(photo instanceof File) || photo.size === 0) return json({ error: "写真を選んでください" }, 400);
  if (!TYPES.includes(photo.type)) return json({ error: "JPEG / PNG / WebP のみ対応です" }, 400);
  if (photo.size > MAX_IMAGE) return json({ error: "写真が大きすぎます（4MBまで）" }, 400);

  const id = `${date.replace(/-/g, "")}-${Date.now().toString(36)}`;
  await images.set(id, await photo.arrayBuffer(), { metadata: { contentType: photo.type } });
  const entry = {
    id,
    title,
    date: date.replace(/-/g, "."),
    place: clip(form.get("place"), 60),
    body: clip(form.get("body"), 1000),
    alt: clip(form.get("alt"), 120) || title,
    image: `/api/log-image/${id}`,
    created: new Date().toISOString(),
  };
  await logs.setJSON(id, entry);
  return json({ ok: true, log: entry });
};

export const config: Config = { path: "/api/log-upload", method: "POST" };
