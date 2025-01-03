import React, { useState, useEffect } from "react";
import "../styles/mealwizard.css";
import { API_BASE_URL } from "../config";

function Wizard({ onComplete }) {
  const [currentStep, setCurrentStep] = useState("alone");
  const [wizardData, setWizardData] = useState({});
  const [reuseData, setReuseData] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE_URL}/management/account`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (res.ok) {
          const backendData = await res.json();
          const savedWizardData = JSON.parse(localStorage.getItem("userData")) || {};
          const combinedData = { ...backendData, ...savedWizardData };
          setWizardData(combinedData);
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    const savedData = JSON.parse(localStorage.getItem("userData"));
    if (savedData) {
      setReuseData(savedData);
    }
  }, []);

  const stepsConfig = {
    reuseMessages: {
      text: "Continue where you left off?",
      includeInJson: true,
      options: [
        { label: "Yes", value: true, next: "reuse" },
        { label: "No", value: false, next: "alone" },
      ],
    },
    reuse: {
      text: "Reusing your previous meal plan...",
      includeInJson: false,
      action: () => {
        const reuseDataToSend = { reuseMessages: true };
        onComplete(reuseDataToSend);
      },
    },
    alone: {
      text: "Are you eating alone?",
      options: [
        { label: "Yes", value: "yes", next: "cravingfor" },
        { label: "No", value: "no", next: "amountofpeople" },
      ],
      includeInJson: false,
    },
    cravingfor: {
      text: "Anything in particular you want to eat?",
      inputType: "text",
      placeholder: "Enter your meal choice",
      next: "timeavailableforcooking",
      includeInJson: true,
    },
    timeavailableforcooking: {
      text: "How long do you want to cook?",
      options: [
        { label: "20m", value: "20mins", next: "mealprepfor" },
        { label: "30m", value: "30mins", next: "mealprepfor" },
        { label: "45m", value: "45mins", next: "mealprepfor" },
        { label: "60m+", value: "60mins+", next: "mealprepfor" },
      ],
      includeInJson: true,
    },
    mealprepfor: {
      text: "How many days do you want to eat this?",
      options: [
        { label: "1 day", value: "1days", next: "submit" },
        { label: "2 days", value: "2days", next: "submit" },
        { label: "3 days", value: "3days", next: "submit" },
      ],
      includeInJson: true,
    },
    amountofpeople: {
      text: "How many people are eating?",
      inputType: "counter",
      next: "cravingfor",
      includeInJson: true,
    },
    submit: {
      text: "Your plan is ready! Here are your answers:",
      includeInJson: false,
      action: () => {
        const finalData = Object.keys(wizardData).reduce((acc, key) => {
          if (stepsConfig[key]?.includeInJson) {
            acc[key] = wizardData[key];
          }
          return acc;
        }, {});
        localStorage.setItem("userData", JSON.stringify(finalData));
        onComplete(finalData);
      },
      display: () => (
        <div className="answers">
          <ul>
            {Object.entries(wizardData).map(([key, val]) => (
              <li key={key}>
                <strong>{key}:</strong> {val}
              </li>
            ))}
          </ul>
        </div>
      ),
    },
  };

  const currentStepConfig = stepsConfig[currentStep];

  useEffect(() => {
    if (currentStep === "submit") {
      stepsConfig.submit.action();
    }
  }, [currentStep]);

  const handleOptionClick = (value, nextStep) => {
    if (nextStep === "reuse") {
      stepsConfig.reuse.action();
    } else {
      if (currentStep === "reuseMessages" && value === "no") {
        setWizardData({});
      }
      setWizardData((prev) => ({ ...prev, [currentStep]: value }));
      setHistory((prevHistory) => [...prevHistory, currentStep]);
      setCurrentStep(nextStep);
    }
  };

  const handleBackClick = () => {
    setHistory((prevHistory) => {
      const updatedHistory = [...prevHistory];
      const previousStep = updatedHistory.pop();
      setWizardData((prevWizardData) => {
        const updatedData = { ...prevWizardData };
        delete updatedData[currentStep];
        return updatedData;
      });
      setCurrentStep(previousStep || "alone");
      return updatedHistory;
    });
  };

  return (
    <div className="mealwizard-container">
      {currentStep === "submit" ? (
        stepsConfig.submit.display()
      ) : (
        <>
          <h3>{currentStepConfig.text}</h3>
          {currentStepConfig.options && (
            <div className="mealwizard-option">
              {currentStepConfig.options.map((opt, i) => (
                <button
                  key={i}
                  className="mealwizard-button"
                  onClick={() => handleOptionClick(opt.value, opt.next)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
          {currentStepConfig.inputType === "text" && (
            <div className="mealwizard-step">
              <input
                className="mealwizard-input"
                type="text"
                placeholder={currentStepConfig.placeholder}
                value={wizardData[currentStep] || ""}
                onChange={(e) =>
                  setWizardData((prev) => ({
                    ...prev,
                    [currentStep]: e.target.value,
                  }))
                }
              />
              <button
                className="mealwizard-button"
                onClick={() => setCurrentStep(currentStepConfig.next)}
                disabled={!wizardData[currentStep]?.trim()}
              >
                Next
              </button>
            </div>
          )}
          {currentStepConfig.inputType === "counter" && (
            <div className="mealwizard-step">
              <button
                className="mealwizard-button"
                onClick={() =>
                  setWizardData((prev) => ({
                    ...prev,
                    amountofpeople: Math.max((prev.amountofpeople || 1) - 1, 1),
                  }))
                }
              >
                -
              </button>
              <input
                className="mealwizard-input"
                type="text"
                value={wizardData.amountofpeople || 1}
                readOnly
              />
              <button
                className="mealwizard-button"
                onClick={() =>
                  setWizardData((prev) => ({
                    ...prev,
                    amountofpeople: (prev.amountofpeople || 1) + 1,
                  }))
                }
              >
                +
              </button>
              <button
                className="mealwizard-button"
                onClick={() => setCurrentStep(currentStepConfig.next)}
              >
                Next
              </button>
            </div>
          )}
          {history.length > 0 && (
            <button className="mealwizard-back-button" onClick={handleBackClick}>
              Back
            </button>
          )}
        </>
      )}
    </div>
  );
}

export default Wizard;
