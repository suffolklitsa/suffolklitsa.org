# hello@suffolklitsa.org

A Cloudflare Email Worker that forwards every message sent to `hello@suffolklitsa.org`
to the whole e-board. Replies go out from each officer's own address.

## Change who gets it (each new board)

1. Cloudflare dashboard, suffolklitsa.org, Email, Email Routing, **Destination addresses**:
   add each new officer. Cloudflare emails them a link; mail only reaches them after they click it.
2. Set the list (comma-separated), from this folder:
   `npx wrangler secret put RECIPIENTS`
3. Remove old officers from Destination addresses.

The routing rule for `hello@` sends to the Worker `litsa-hello-forward`. Deploy code
changes with `npx wrangler deploy` from this folder.
