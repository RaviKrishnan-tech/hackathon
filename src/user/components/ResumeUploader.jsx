import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { setDoc, doc } from "firebase/firestore";
import { db } from "../../firebaseConfig";

export default function ResumeUploader() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user"));

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first!");
    if (!user || !user.uid) {
      console.error("❌ User is not defined:", user);
      alert("User not logged in. Please log in again.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/resume/process", {
        method: "POST",
        body: formData,
        mode: "cors",
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Server responded with error:", err);
        throw new Error("Server error: " + err);
      }

      const data = await res.json();
      const skills = data.technical_skills;

      if (!skills || skills.length === 0) {
        alert("⚠️ No technical skills found. Please upload a better resume.");
        return;
      }

      // Save skills to Firebase
      await setDoc(
        doc(db, "userProgress", user.uid),
        { skills },
        { merge: true }
      );

      // Store in localStorage for further use
      localStorage.setItem("userSkills", JSON.stringify(skills));

      alert("✅ Resume uploaded and skills extracted successfully!");
      navigate("/assessment"); // ✅ Corrected path
    } catch (err) {
      console.error("❌ Upload failed:", err);
      alert("Upload failed. Please check the console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>📄 Upload Your Resume</h2>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? (
          <>
            <span className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full inline-block" />
            Uploading...
          </>
        ) : (
          "Upload"
        )}
      </button>
    </div>
  );
}
