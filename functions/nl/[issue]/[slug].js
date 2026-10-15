// Tracked newsletter links: suffolklitsa.org/nl/<issue>/<slug>.
// Looks the link up in newsletter_links.json, records the click in Counterscale as a view of
// /nl/<issue>/<slug> (the same place the rest of the site's numbers live), then redirects.
// Only links listed in the file redirect anywhere, so this is not an open redirect. Our own
// pages get ?source=newsletter-<issue> so the visit is attributed too.
import LINKS from "../../../newsletter_links.json";

export async function onRequest({ request, params, waitUntil }) {
  const issue = String(params.issue || "");
  const slug = String(params.slug || "");
  const table = LINKS[issue];
  const dest = table && typeof table === "object" ? table[slug] : undefined;

  let to = "/?source=newsletter";
  if (dest) {
    to = dest.startsWith("/")
      ? dest + (dest.includes("?") ? "&" : "?") + "source=" + encodeURIComponent("newsletter-" + issue)
      : dest;
    if (request.method === "GET") {
      const u = "https://analytics.suffolklitsa.org/collect?sid=litsa" +
        "&h=" + encodeURIComponent("https://suffolklitsa.org") +
        "&p=" + encodeURIComponent("/nl/" + issue + "/" + slug) +
        "&r=" + encodeURIComponent("newsletter-" + issue);
      waitUntil(fetch(u, { headers: { "User-Agent": request.headers.get("User-Agent") || "" } })
        .catch(() => {}));
    }
  }
  return Response.redirect(new URL(to, request.url).toString(), 302);
}
