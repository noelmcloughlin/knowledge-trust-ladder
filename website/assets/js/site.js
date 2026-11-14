// The site's own script. Everything it does is an addition: with no script
// the pages, the navigation and its headings still work.

// The reader's choices in the Display menu, kept in this browser. They are
// applied before the page is drawn, so a dark page never flashes light.
const root = document.documentElement;
const defaults = { theme: "auto", size: "large" };
const prefs = { ...defaults };
try {
  Object.assign(prefs, JSON.parse(localStorage.getItem("ktl-display") || "{}"));
} catch {}

function applyPrefs() {
  root.dataset.theme = prefs.theme;
  root.dataset.size = prefs.size;
  // A figure with a dark version, and the code colours, follow the choice too.
  const media = { auto: "(prefers-color-scheme: dark)", dark: "all", light: "not all" }[prefs.theme];
  for (const el of document.querySelectorAll('source[media*="prefers-color-scheme"], source[data-dark], #code-dark')) {
    el.dataset.dark = "";
    el.media = media;
  }
  // The graph page draws on a canvas, which takes its colours again on this.
  document.dispatchEvent(new Event("displaychange"));
}
applyPrefs();

addEventListener("DOMContentLoaded", () => {
  const menu = document.getElementById("prefs");
  document.getElementById("prefs-open").hidden = false;
  // A choice this browser kept from an older menu, such as a size no longer offered, falls back to the default.
  for (const name of ["theme", "size"]) {
    const offered = [...menu.querySelectorAll(`input[name="${name}"]`)].map((input) => input.value);
    if (!offered.includes(prefs[name])) prefs[name] = defaults[name];
  }
  for (const input of menu.querySelectorAll("input")) {
    input.checked = prefs[input.name] === input.value;
    input.addEventListener("change", () => {
      prefs[input.name] = input.value;
      try {
        localStorage.setItem("ktl-display", JSON.stringify(prefs));
      } catch {}
      applyPrefs();
    });
    // A choice made by pointer closes the menu. One made with the arrow keys leaves it open, since each key press chooses, and Escape closes it.
    input.addEventListener("click", (event) => event.detail && menu.hidePopover());
  }
  // Again now the page is read, for its figures and for a choice that fell back.
  applyPrefs();

  // The navigation is built once per group, so the current page's link is marked here.
  // A page that retells another has no link of its own, and the page it retells is marked.
  const links = [...document.querySelectorAll("#nav a")].filter((a) => !a.hash);
  const here = [location.pathname, new URL(document.getElementById("main").dataset.retells ?? "", location).pathname];
  for (const a of links.filter((a) => a.pathname === here.find((path) => links.some((link) => link.pathname === path)))) {
    a.setAttribute("aria-current", "page");
    a.scrollIntoView({ block: "nearest" });
  }

  // A Copy button on each code block.
  for (const pre of document.querySelectorAll(".prose pre:not(.mermaid)")) {
    const button = Object.assign(document.createElement("button"), { type: "button", className: "copy", textContent: "Copy" });
    button.addEventListener("click", async () => {
      await navigator.clipboard.writeText((pre.querySelector("code") ?? pre).innerText);
      button.textContent = "Copied";
      setTimeout(() => (button.textContent = "Copy"), 1500);
    });
    pre.append(button);
  }

  // A figure opens over the page as large as the window allows, by mouse or keyboard. A click, Escape or
  // Close puts it away, so the reader never leaves the page. The link still names the file, for a new tab.
  let zoom;
  for (const img of document.querySelectorAll(".prose picture > img, .prose p > img")) {
    if (img.closest("a") || img.width < 200) continue;
    const link = Object.assign(document.createElement("a"), { href: img.currentSrc || img.src, className: "figure", title: "Show the figure at full size" });
    (img.closest("picture") ?? img).replaceWith(link);
    link.append(img.closest("picture") ?? img);
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (!zoom) {
        zoom = Object.assign(document.createElement("dialog"), { className: "zoom", ariaLabel: "The figure at full size" });
        zoom.innerHTML = '<button type="button">Close</button><img alt="">';
        zoom.addEventListener("click", () => zoom.close());
        document.body.append(zoom);
      }
      const big = zoom.querySelector("img");
      const src = img.currentSrc || img.src;
      // A drawing grows to fill the window. A photograph stops at its own size, where it is still sharp.
      const drawing = /\.svg([?#]|$)/i.test(src);
      Object.assign(big, { src, alt: img.alt, className: drawing ? "zoom__drawing" : "" });
      big.style.maxWidth = drawing ? "" : `min(100%, ${img.naturalWidth}px)`;
      zoom.showModal();
    });
  }

  // Search, once a build has written its index. The preview server has none.
  // Each library is looked for by its type, since an element whose id is
  // its name would otherwise stand in for it.
  const search = document.getElementById("search");
  if (typeof window.PagefindUI === "function") {
    new PagefindUI({ element: search, bundlePath: search.dataset.bundle, showSubResults: true, showImages: false, resetStyles: false });
    search.querySelector("input")?.setAttribute("aria-label", "Search this site");
    // A click on the dimmed page closes the results, as Escape in the box does.
    document.addEventListener("click", (event) => {
      if (!search.contains(event.target) && search.querySelector(".pagefind-ui__drawer:not(.pagefind-ui__hidden)")) search.querySelector(".pagefind-ui__search-clear")?.click();
    });
  }

  // A diagram takes the page's own paper, ink and lines, in the scheme the reader chose.
  if (typeof window.mermaid?.initialize === "function") {
    const css = getComputedStyle(document.body);
    const probe = document.body.appendChild(document.createElement("span"));
    const color = (name) => {
      probe.style.color = `var(${name})`;
      return getComputedStyle(probe).color;
    };
    const themeVariables = {
      darkMode: matchMedia("(prefers-color-scheme: dark)").matches ? prefs.theme !== "light" : prefs.theme === "dark",
      fontFamily: css.fontFamily,
      background: color("--bg"),
      primaryColor: color("--card"),
      primaryTextColor: color("--fg"),
      primaryBorderColor: color("--rule"),
      secondaryColor: color("--panel"),
      tertiaryColor: color("--panel"),
      lineColor: color("--muted"),
      textColor: color("--fg"),
    };
    probe.remove();
    mermaid.initialize({ startOnLoad: true, theme: "base", themeVariables });
  }
});
