// hello@suffolklitsa.org: forwards each message to every e-board member.
// The list is the RECIPIENTS secret (comma-separated), not this file, so board addresses
// stay out of the public repo. Each address must be a verified destination in Cloudflare
// Email Routing; an unverified one is skipped and logged, and the rest still get the mail.
export default {
  async email(message, env) {
    const to = [...new Set((env.RECIPIENTS || "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean))];
    const failed = [];
    for (const addr of to) {
      try {
        await message.forward(addr);
      } catch (e) {
        failed.push(addr);
        console.log("forward failed", addr, String((e && e.message) || e));
      }
    }
    if (to.length === 0 || failed.length === to.length) {
      message.setReject("This address could not deliver your message. Please email sam.darkwa@su.suffolk.edu.");
    }
  },
};
