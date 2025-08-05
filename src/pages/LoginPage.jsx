// src/pages/LoginPage.jsx
import { useState } from "react";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth";
import { auth } from "../firebaseConfig";
import { getDoc, doc } from "firebase/firestore";
import { db } from "../firebaseConfig";
import "../styles.css";

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      let userCredential;
      if (isSignUp) {
        userCredential = await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );
        console.log("User signed up:", userCredential.user);
      } else {
        userCredential = await signInWithEmailAndPassword(
          auth,
          email,
          password
        );
        console.log("Logged in:", userCredential.user);
      }
      onLogin(userCredential.user);
    } catch (err) {
      console.error("Auth Error:", err);
      if (err.code === "auth/email-already-in-use") {
        setError("Email already in use. Please log in.");
      } else if (err.code === "auth/user-not-found") {
        setError("No account found. Please sign up.");
      } else if (err.code === "auth/wrong-password") {
        setError("Incorrect password. Try again.");
      } else if (err.code === "auth/invalid-email") {
        setError("Invalid email format.");
      } else if (err.code === "auth/weak-password") {
        setError("Password should be at least 6 characters.");
      } else {
        setError("Authentication failed. Please try again.");
      }
    }
  };

  const loadUserData = async (user) => {
    // Profile
    const profileSnap = await getDoc(doc(db, "userProfiles", user.uid));
    const profile = profileSnap.exists() ? profileSnap.data() : null;

    // Progress
    const progressSnap = await getDoc(doc(db, "userProgress", user.uid));
    const progress = progressSnap.exists() ? progressSnap.data() : null;

    return { profile, progress };
  };

  return (
    <div className="login-container">
      <h1 className="login-title">{isSignUp ? "Sign Up" : "Login"}</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error-text">{error}</p>}
        <button type="submit">{isSignUp ? "Sign Up" : "Login"}</button>
      </form>
      <button
        style={{
          marginTop: 10,
          background: "none",
          color: "#2563eb",
          border: "none",
          cursor: "pointer",
        }}
        onClick={() => {
          setIsSignUp((prev) => !prev);
          setError("");
        }}
      >
        {isSignUp
          ? "Already have an account? Login"
          : "New user? Sign Up"}
      </button>
    </div>
  );
}
