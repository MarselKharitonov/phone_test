"use strict";

const $ = (id) => document.getElementById(id);
const frameNames = {
  shoulders: "фото по плечи или с частично видимым торсом",
  waist: "фото по пояс",
  full: "фото в полный рост",
};
const categoryNames = { tops: "верх", bottoms: "низ", "one-pieces": "платье или комбинезон" };

function updateCategories() {
  const partial = $("frame").value !== "full";
  for (const option of $("category").options) option.disabled = partial && option.value !== "tops";
  if (partial && $("category").value !== "tops") $("category").value = "tops";
}

function makePrompt(data) {
  const fields = [
    `Кадр: ${frameNames[data.frame]}.`,
    `Категория вещи: ${categoryNames[data.category]}.`,
    `Стиль: ${data.style}. Предпочитаемая посадка: ${data.fit}.`,
    `Сезон: ${data.season}.`,
  ];
  if (data.location) fields.push(`Локация: ${data.location}.`);
  if (data.budget) fields.push(`Ориентировочный бюджет: ${data.budget} ₽; не придумывай цены и товары.`);
  if (data.item) fields.push(`Название вещи: ${data.item}.`);
  if (data.notes) fields.push(`Дополнительные пожелания: ${data.notes}.`);
  return [
    "Создай реалистичную виртуальную примерку на основе двух прикреплённых изображений.",
    "Первое изображение — фотография человека, второе — фотография конкретной вещи. Верни изображение того же человека в этой вещи.",
    ...fields,
    "Сохрани исходные границы кадра, соотношение сторон, позу, лицо, тело, волосы, руки, освещение и фон. Не расширяй кадр и не дорисовывай невидимые части тела.",
    "Меняй одежду исключительно в видимой зоне, относящейся к указанной категории. Если кадр по плечи или по пояс, не добавляй брюки, ноги или обувь. Не меняй остальную одежду.",
    "Передай вещь максимально близко к фотографии товара: цвет, крой, длину, материал, фактуру, принт, карманы и видимые детали. Не добавляй другие вещи и не подменяй дизайн.",
    "Сохрани естественную анатомию и реалистичную посадку без утверждений о точном размере. Если корректно выполнить примерку невозможно, сообщи об этом вместо выдумывания результата.",
  ].join("\n\n");
}

for (const id of ["person", "garment", "result"]) {
  let previous;
  $(id).addEventListener("change", () => {
    if (previous) URL.revokeObjectURL(previous);
    const image = $(`${id}-preview`);
    const file = $(id).files[0];
    if (!file || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      image.hidden = true;
      image.removeAttribute("src");
      if (file) $("status").textContent = "Выберите изображение JPG, PNG или WEBP.";
      return;
    }
    previous = URL.createObjectURL(file);
    image.src = previous;
    image.hidden = false;
  });
}
$("frame").addEventListener("change", updateCategories);
updateCategories();

$("styling-form").addEventListener("input", () => {
  if ($("prompt").value) {
    $("prompt").value = "";
    $("copy").disabled = true;
    $("status").textContent = "Параметры изменились. Создайте промпт заново.";
  }
});

$("styling-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!$("ack").checked) {
    $("status").textContent = "Подтвердите, что понимаете порядок ручной передачи фото.";
    $("ack").focus();
    return;
  }
  const data = Object.fromEntries(["frame", "category", "style", "fit", "season", "location", "budget", "item", "notes"].map((id) => [id, $(id).value.trim()]));
  $("prompt").value = makePrompt(data);
  $("copy").disabled = false;
  $("status").textContent = "Промпт готов. Не забудьте прикрепить оба изображения в чат.";
});

$("copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText($("prompt").value);
    $("status").textContent = "Промпт скопирован.";
  } catch {
    $("prompt").focus();
    $("prompt").select();
    $("status").textContent = "Не удалось скопировать автоматически. Текст выделен — скопируйте его вручную.";
  }
});
