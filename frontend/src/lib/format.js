export const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

export const number = (value) => new Intl.NumberFormat("en-IN").format(Number(value || 0));

export const dateTime = (value) =>
  new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

export const apiError = (error, fallback = "Something went wrong") =>
  error.response?.data?.detail || error.message || fallback;

