import assert from "node:assert/strict";
import test from "node:test";
import { analyzePrices, classify, percentChange } from "./price-analytics.js";

const series = (prices) => prices.map((price, hour) => ({ price, hour, date: `${hour}:00` }));

test("calculates average, minimum, maximum and variation", () => {
  const stats = analyzePrices(series([10, 20, 30]));
  assert.equal(stats.average, 20); assert.equal(stats.minimum.price, 10); assert.equal(stats.maximum.price, 30);
  assert.equal(stats.absoluteChange, 10); assert.equal(stats.percentageChange, 50); assert.equal(stats.trend, "positive");
});
test("detects negative and neutral trends", () => {
  assert.equal(analyzePrices(series([30, 20])).trend, "negative");
  assert.equal(analyzePrices(series([10, 10.04])).trend, "neutral");
});
test("supports empty, zero and negative prices", () => {
  assert.equal(analyzePrices([]), null); assert.equal(percentChange(0, 10), null);
  const stats = analyzePrices(series([-10, 0, 10])); assert.equal(stats.average, 0); assert.equal(stats.minimum.price, -10);
});
test("classifies using period quartiles", () => {
  assert.equal(classify(1, 2, 8), "Bajo"); assert.equal(classify(5, 2, 8), "Medio"); assert.equal(classify(9, 2, 8), "Alto");
});
test("generates deterministic insights and suggestion", () => {
  const stats = analyzePrices(series([30, 20, 10]));
  assert.ok(stats.insights.items.some((item) => item.title.includes("bajista")));
  assert.ok(stats.insights.suggestion.includes("menor precio"));
});
