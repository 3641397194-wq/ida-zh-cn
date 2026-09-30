// Fills every .hexwall element with a deterministic hex-dump. The bytes of "汉化" (UTF-8) are planted in amber.
(function () {
  let seed = 0x1DA9;                              // deterministic: same picture on every build
  const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  const hex = n => n.toString(16).toUpperCase().padStart(2, "0");
  const HANHUA = [0xE6, 0xB1, 0x89, 0xE5, 0x8C, 0x96];          // 汉 化
  const WORDS = "File Edit Jump Search View Debugger Options Windows Help".split(" ");

  document.querySelectorAll(".hexwall").forEach(el => {
    const rows = parseInt(el.dataset.rows || "30", 10);
    const cols = parseInt(el.dataset.cols || "1", 10);
    const plant = new Set([Math.floor(rows * 0.36), Math.floor(rows * 0.71)]);
    let out = "";
    for (let r = 0; r < rows; r++) {
      const parts = [];
      for (let c = 0; c < cols; c++) {
        const addr = (0x140001000 + (r + c * rows) * 16).toString(16).toUpperCase().padStart(9, "0");
        const bytes = Array.from({ length: 16 }, () => Math.floor(rnd() * 256));
        let startPlant = -1;
        if (c === Math.min(1, cols - 1) && plant.has(r)) {
          startPlant = 3 + Math.floor(rnd() * 6);
          HANHUA.forEach((b, i) => (bytes[startPlant + i] = b));
        }
        const cells = bytes.map((b, i) => {
          const s = hex(b);
          return startPlant >= 0 && i >= startPlant && i < startPlant + 6 ? "<b>" + s + "</b>" : s;
        });
        const ascii = bytes.map(b => (b >= 0x20 && b < 0x7f ? String.fromCharCode(b) : ".")).join("");
        parts.push(addr + "  " + cells.slice(0, 8).join(" ") + "  " + cells.slice(8).join(" ") + "  |" + ascii.replace(/</g, "&lt;") + "|");
      }
      out += parts.join("      ") + "\n";
    }
    el.innerHTML = out;
  });
})();
