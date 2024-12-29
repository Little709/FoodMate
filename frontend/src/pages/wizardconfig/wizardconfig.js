const stepsConfig = {
  start: {
    text: "Are you eating alone?",
    options: [
      { label: "Yes", value: "yes", next: "alone" },
      { label: "No", value: "no", next: "group" },
    ],
  },
  alone: {
    text: "What do you want to eat?",
    input: { placeholder: "Enter your meal choice" },
    next: "drink",
  },
  group: {
    text: "How many people are eating?",
    input: { type: "number", placeholder: "Enter number" },
    next: "submit",
  },
  drink: {
    text: "Would you like a drink with that?",
    options: [
      { label: "Yes", value: "drink_yes", next: "submit" },
      { label: "No", value: "drink_no", next: "submit" },
    ],
  },
};

export default stepsConfig;


