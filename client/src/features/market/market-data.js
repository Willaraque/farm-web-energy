const PRICE_KEYS = ["price", "Precio_Espanol", "Precio_Español", "value"];

function parsePrice(value) {
  if (typeof value === "number") {
    return Number.isFinite(value) ? value : null;
  }

  if (typeof value !== "string") return null;

  const normalizedValue = value.trim().replace(",", ".");
  const price = Number(normalizedValue);
  return Number.isFinite(price) ? price : null;
}

export function getMarketPrice(row) {
  for (const key of PRICE_KEYS) {
    const price = parsePrice(row?.[key]);
    if (price !== null) return price;
  }

  const priceEntry = Object.entries(row ?? {}).find(([key]) => {
    const normalizedKey = key
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z]/gi, "")
      .toLowerCase();

    return normalizedKey.startsWith("precioespa") || normalizedKey === "price";
  });

  return priceEntry ? parsePrice(priceEntry[1]) : null;
}

export function createMarketSeries(rows, market = "diario") {
  if (!Array.isArray(rows)) return [];

  return rows.flatMap((row) => {
    const rowMarket = String(row.Mercado ?? row.market ?? "").toLowerCase();
    const isRequestedMarket =
      !rowMarket ||
      rowMarket === market ||
      (market === "diario" && rowMarket === "daily");

    if (!isRequestedMarket) return [];

    const price = getMarketPrice(row);
    if (price === null) return [];

    return [{ date: row.Hora ?? row.Fecha ?? row.date, price }];
  });
}

export function calculatePriceStats(values) {
  if (!Array.isArray(values)) return null;

  const prices = values
    .map((value) =>
      typeof value === "number" ? value : getMarketPrice(value),
    )
    .filter(Number.isFinite);

  if (!prices.length) return null;

  return {
    average: prices.reduce((total, price) => total + price, 0) / prices.length,
    minimum: Math.min(...prices),
    maximum: Math.max(...prices),
  };
}
