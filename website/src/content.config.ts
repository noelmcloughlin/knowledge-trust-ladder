import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { docsLoader } from "@astrojs/starlight/loaders";
import { docsSchema } from "@astrojs/starlight/schema";

// scripts/sync.mjs writes every page under src/content/docs/. The extra keys
// say which repository file a page was rendered from, and carry what a
// concept page shows above its body.
const link = z.object({ text: z.string(), href: z.string() });

const concept = z.object({
  id: z.string(),
  iri: z.string(),
  type: z.string(),
  group: z.string(),
  status: z.string().optional(),
  label: z.string(),
  tone: z.enum(["person", "edited", "automation", "nobody", "retired"]),
  definition: z.string().optional(),
  reviewBy: z.string().optional(),
  tags: z.array(z.string()).default([]),
  generated: z.object({ by: z.string(), at: z.string() }).optional(),
  verified: z.array(z.object({ by: z.string(), at: z.string(), note: z.string().optional() })).default([]),
  sources: z.array(link).default([]),
  relations: z.array(z.object({ name: z.string(), targets: z.array(link) })).default([]),
  incoming: z.array(z.object({ name: z.string(), from: link })).default([]),
  files: z.object({ markdown: z.string(), jsonld: z.string(), github: z.string() }),
});

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        ktlSource: z.string().optional(),
        ktlShiftHeadings: z.boolean().optional(),
        lokf: concept.optional(),
      }),
    }),
  }),
};
