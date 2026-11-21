// Fetch the visitor count from the API and show it in the footer.
fetch("https://47shfsv4xh.execute-api.ap-south-1.amazonaws.com/count")
  .then(function (r) { return r.json(); })
  .then(function (data) {
    document.getElementById("visitor-count").textContent = data.count;
  })
  .catch(function () {
    document.getElementById("visitor-count").textContent = "unavailable";
  });
