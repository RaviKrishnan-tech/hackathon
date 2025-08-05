import { useState } from "react";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { setDoc, doc } from "firebase/firestore";
import { auth, db } from "../firebaseConfig";

export default function SignUpPage({ onSignUp }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [gender, setGender] = useState("");
  const [error, setError] = useState("");

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      // Save profile details
      await setDoc(doc(db, "userProfiles", user.uid), {
        name,
        dob,
        gender,
        email: user.email,
      });
      // Optionally, initialize progress
      await setDoc(doc(db, "userProgress", user.uid), {
        resumeUploaded: false,
        extractedSkills: [],
        assessmentTaken: false,
      });
      onSignUp(user);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSignUp}>
      <input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
      <input type="date" placeholder="Date of Birth" value={dob} onChange={e => setDob(e.target.value)} required />
      <select value={gender} onChange={e => setGender(e.target.value)} required>
        <option value="">Select Gender</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="other">Other</option>
      </select>
      <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
      <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
      {error && <p style={{color: "red"}}>{error}</p>}
      <button type="submit">Sign Up</button>
    </form>
  );
}