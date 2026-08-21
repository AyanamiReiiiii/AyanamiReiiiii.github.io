/* Renders writing lists from writings.js.
   Usage: renderWritings(element, { category: "math", limit: 8 })
   - no category  → all writings (e.g. the home page)
   - no limit     → everything in that category */

(function () {
  var LABELS = { math: "Math", cs: "CS", thoughts: "Thoughts" };

  window.renderWritings = function (listEl, opts) {
    opts = opts || {};
    var items = (window.WRITINGS || []).slice();

    if (opts.category) {
      items = items.filter(function (w) { return w.category === opts.category; });
    }

    items.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });

    if (opts.limit) items = items.slice(0, opts.limit);

    items.forEach(function (w) {
      var li = document.createElement("li");

      var date = document.createElement("span");
      date.className = "date";
      date.textContent = w.date;

      var item = document.createElement("div");
      item.className = "item";

      var a = document.createElement("a");
      a.textContent = w.title;
      a.href = w.file;
      if (/\.pdf$/i.test(w.file)) {
        a.target = "_blank";
        a.rel = "noopener";
      }
      item.appendChild(a);

      if (w.desc) {
        var d = document.createElement("span");
        d.className = "desc";
        d.textContent = w.desc;
        item.appendChild(d);
      }

      li.appendChild(date);
      li.appendChild(item);
      listEl.appendChild(li);
    });
  };
})();
