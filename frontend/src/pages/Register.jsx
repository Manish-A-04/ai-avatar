import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";

export const Register = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await register(email, password, username);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to register. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[80vh]">
      <div className="w-full max-w-md p-8 glass-panel rounded-xl">
        <div className="text-center mb-8">
          <div className="inline-flex w-12 h-12 bg-white rounded-full items-center justify-center text-black font-bold text-xl mb-4">
            A
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Create an account</h1>
          <p className="text-gray-400 text-sm mt-2">Join us to start creating AI avatars</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Username (alphanumeric)"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            placeholder="johndoe"
            pattern="[a-zA-Z0-9_]+"
            title="Only alphanumeric characters and underscores are allowed"
          />
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="you@example.com"
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
          />

          {error && <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md text-red-400 text-sm">{error}</div>}

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Register
          </Button>
        </form>

        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-white hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};
