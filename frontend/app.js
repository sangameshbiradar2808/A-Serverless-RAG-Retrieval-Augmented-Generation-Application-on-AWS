const askButton = document.getElementById("askButton");
const questionInput = document.getElementById("question");
const statusEl = document.getElementById("status");
const answerPanel = document.getElementById("answerPanel");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");

function showSources(citations) {
  sourcesEl.replaceChildren();
  const refs = (citations || []).flatMap(c => c.sources || []);
  if (!refs.length) {
    sourcesEl.textContent = "No source references were returned.";
    return;
  }
  refs.forEach(ref => {
    const item = document.createElement("div");
    item.className = "source";
    const source = document.createElement("strong");
    source.textContent = ref.source || "Document source";
    const passage = document.createElement("p");
    passage.textContent = ref.text || "";
    item.append(source, passage);
    sourcesEl.append(item);
  });
}

askButton.addEventListener("click", async () => {
  const question = questionInput.value.trim();
  if (!question) {
    statusEl.textContent = "Enter a question first.";
    return;
  }
  const apiUrl = window.APP_CONFIG?.API_URL;
  if (!apiUrl || apiUrl.includes("YOUR_API_ID")) {
    statusEl.textContent = "Configure API_URL in config.js first.";
    return;
  }

  askButton.disabled = true;
  statusEl.textContent = "Thinking…";
  answerPanel.classList.remove("hidden");
  answerEl.textContent = "";
  sourcesEl.textContent = "";

  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    answerEl.textContent = data.answer || "No answer returned.";
    showSources(data.citations);
    statusEl.textContent = "Answer ready";
  } catch (error) {
    answerEl.textContent = error.message;
    statusEl.textContent = "Request failed";
  } finally {
    askButton.disabled = false;
  }
});
