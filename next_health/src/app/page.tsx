"use client";

import React, { useState } from "react";
import LoginRegisterForm from "@/components/LoginRegisterForm";
import { FaBars, FaTimes } from "react-icons/fa";

const LandingPage = () => {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isClosing, setIsClosing] = useState<boolean>(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleCloseModal = () => {
    setIsClosing(true);
    setTimeout(() => {
      setShowLoginModal(false);
      setIsClosing(false);
    }, 270);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Navbar */}
      <nav className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          {/* Mobile Menu Toggle Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden text-2xl focus:outline-none"
          >
            {isMobileMenuOpen ? <FaTimes /> : <FaBars />}
          </button>
          {/* Logo and Brand Name */}
          <div className="flex items-center">
            <img
              src="/logo.png"
              alt="TeleHealth Logo"
              className="h-10 w-10 mr-2"
            />
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex space-x-6">
            <a href="#home" className="hover:text-blue-200 transition duration-300 px-8 nm">
              خانه
            </a>
            <a href="#services" className="hover:text-blue-200 transition duration-300 px-8 nm">
              خدمات
            </a>
            <a href="#about" className="hover:text-blue-200 transition duration-300 px-8 nm">
              درباره ما
            </a>
            <a href="#contact" className="hover:text-blue-200 transition duration-300 px-8 nm">
              تماس با ما
            </a>
          </div>

          {/* Login/Register Button (Desktop and Mobile) */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowLoginModal(true)}
              className="bg-white text-blue-600 px-4 py-2 rounded hover:bg-blue-50 transition duration-300"
            >
              ورود / ثبت نام
            </button>

          </div>
        </div>
      </nav>

      {/* Mobile Sidebar */}
      <div
        className={`fixed inset-y-0 right-0 w-64 bg-blue-600 text-white transform transition-transform duration-300 ease-in-out ${isMobileMenuOpen ? "translate-x-0" : "translate-x-full"
          }`}
      >
        {/* Close Button */}
        <button
          onClick={toggleMobileMenu}
          className="absolute top-4 left-4 text-2xl focus:outline-none"
        >
          <FaTimes />
        </button>

        {/* Sidebar Content */}
        <div className="p-4 mt-12">
          <a
            href="#home"
            className="block py-2 px-4 hover:bg-blue-500 transition duration-300"
          >
            خانه
          </a>
          <a
            href="#services"
            className="block py-2 px-4 hover:bg-blue-500 transition duration-300"
          >
            خدمات
          </a>
          <a
            href="#about"
            className="block py-2 px-4 hover:bg-blue-500 transition duration-300"
          >
            درباره ما
          </a>
          <a
            href="#contact"
            className="block py-2 px-4 hover:bg-blue-500 transition duration-300"
          >
            تماس با ما
          </a>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center p-4">
        <h2 className="text-4xl md:text-5xl font-bold text-center text-gray-800 mb-6 animate-fade-in">
          Welcome to TeleHealth!
        </h2>
        <p className="text-lg text-gray-600 text-center mb-8 max-w-2xl">
          Experience the future of healthcare with our telemedicine platform. Connect with top doctors, schedule appointments, and get personalized care from the comfort of your home.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h3 className="text-xl font-semibold text-blue-600 mb-2">24/7 Access</h3>
            <p className="text-gray-600">Get medical advice anytime, anywhere.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h3 className="text-xl font-semibold text-blue-600 mb-2">Expert Doctors</h3>
            <p className="text-gray-600">Consult with certified healthcare professionals.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h3 className="text-xl font-semibold text-blue-600 mb-2">Easy Scheduling</h3>
            <p className="text-gray-600">Book appointments with just a few clicks.</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center">
        &copy; 2025 تله هلت. All rights reserved.
      </footer>

      {showLoginModal && (
        <div className="overlay" onClick={handleCloseModal}>
          <div
            className={`${isClosing ? 'fade-out' : 'fade-in'}`}
            onClick={(e) => e.stopPropagation()}
          >
            <LoginRegisterForm onClose={handleCloseModal} />
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;