import { defineRouteMiddleware } from "@astrojs/starlight/route-data";

// On a concept page the top of the page is the concept's record, and its body
// usually starts with its own "Overview", so the contents list names the top
// "Record" rather than showing "Overview" twice.
export const onRequest = defineRouteMiddleware((context) => {
  const route = context.locals.starlightRoute;
  const first = route.toc?.items[0];
  if (route.entry.data.lokf && first) first.text = "Record";
});
