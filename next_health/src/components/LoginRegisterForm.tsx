import React, { useState } from "react";
import axios from "axios";
import "../statics/css/LoginRegisterForm.css"; // Import the CSS file

interface LoginRegisterFormProps {
  onClose: () => void;
}

const LoginRegisterForm: React.FC<LoginRegisterFormProps> = ({ onClose }) => {
  const [phoneOrEmail, setPhoneOrEmail] = useState<string>("");
  const [otp, setOtp] = useState<string>("");
  const [isIranian, setIsIranian] = useState<boolean>(true);
  const [nationalId, setNationalId] = useState<string>("");
  const [passportId, setPassportId] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isOtpSent, setIsOtpSent] = useState<boolean>(false);
  const [identifier, setIdentifier] = useState<string>("");

  // Helper function to handle API calls
  const handleApiCall = async (url: string, data: any) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await axios.post(url, data);
      return response.data;
    } catch (err: any) {
      // Extract error message from response
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "An error occurred. Please try again.";
      setError(errorMessage);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = {
      phone_number: isIranian ? phoneOrEmail : "",
      email: !isIranian ? email : "",
      // role is fixed as 'patient' in this example; adjust as needed
      role: "patient",
      is_iranian: isIranian,
      national_id: isIranian ? nationalId : "",
      passport_id: !isIranian ? passportId : "",
    };

    try {
      const response = await handleApiCall(
        "http://localhost:8000/api/auth/register/",
        data
      );
      setIsOtpSent(true);
      setIdentifier(response.identifier); // Assumes your backend returns an "identifier"
      console.log("OTP sent successfully. Identifier:", response.identifier);
    } catch (err) {
      console.error("Error during registration:", err);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = { otp, identifier };

    try {
      const response = await handleApiCall(
        "http://localhost:8000/api/auth/verify-otp/",
        data
      );
      alert("User authenticated successfully!");
      onClose(); // Close modal after successful verification
    } catch (err) {
      console.error("Error during OTP verification:", err);
    }
  };

  // Toggle between Iranian and non-Iranian forms
  const toggleIsIranian = () => {
    setIsIranian((prev) => !prev);
    // Optionally reset some fields if switching between forms
    setError(null);
    setPhoneOrEmail("");
    setEmail("");
    setNationalId("");
    setPassportId("");
  };

  return (
    <div className={`form-container ${isIranian ? "rotate-0" : "rotate-180"}`}>
      {/* Inner container rotates back to keep content legible */}
      <div className={`inner-container ${isIranian ? "" : "rotate-180"}`}>
        <h2 className="text-xl font-bold text-center mb-4">
          ورود / ثبت نام
        </h2>
        <form onSubmit={isOtpSent ? handleOtpSubmit : handleSubmit}>
          {!isOtpSent ? (
            <>
              <div className="mb-4">
                <label className="inline-flex items-center text-sm font-medium">
                  <input
                    type="checkbox"
                    checked={isIranian}
                    onChange={toggleIsIranian}
                    className="form-checkbox"
                  />
                  <span className="ml-2">ایرانی هستید؟</span>
                </label>
              </div>

              {isIranian ? (
                <>
                  <div className="mb-4">
                    <label
                      htmlFor="phoneOrEmail"
                      className="block text-sm font-medium"
                    >
                      شماره تلفن
                    </label>
                    <input
                      id="phoneOrEmail"
                      type="text"
                      value={phoneOrEmail}
                      onChange={(e) => setPhoneOrEmail(e.target.value)}
                      className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                      required
                      aria-label="شماره تلفن"
                    />
                  </div>

                  <div className="mb-4">
                    <label
                      htmlFor="nationalId"
                      className="block text-sm font-medium"
                    >
                      کد ملی
                    </label>
                    <input
                      id="nationalId"
                      type="text"
                      value={nationalId}
                      onChange={(e) => setNationalId(e.target.value)}
                      className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                      required
                      aria-label="کد ملی"
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-4">
                    <label
                      htmlFor="email"
                      className="block text-sm font-medium"
                    >
                      ایمیل
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                      required
                      aria-label="ایمیل"
                    />
                  </div>
                  <div className="mb-4">
                    <label
                      htmlFor="passportId"
                      className="block text-sm font-medium"
                    >
                      شماره گذرنامه
                    </label>
                    <input
                      id="passportId"
                      type="text"
                      value={passportId}
                      onChange={(e) => setPassportId(e.target.value)}
                      className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                      required
                      aria-label="شماره گذرنامه"
                    />
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="mb-4">
              <label
                htmlFor="otp"
                className="block text-sm font-medium"
              >
                کد تایید
              </label>
              <input
                id="otp"
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="mt-1 p-2 border border-gray-300 rounded-md w-full"
                required
                aria-label="کد تایید"
              />
            </div>
          )}

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            type="submit"
            className={`mt-4 p-2 bg-blue-600 text-white rounded-md w-full ${
              isSubmitting ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={isSubmitting}
          >
            {isOtpSent ? "تایید کد" : "ارسال کد"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="mt-4 text-blue-600 text-sm w-full text-center"
          >
            بستن
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginRegisterForm;