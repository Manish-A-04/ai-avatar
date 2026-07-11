import React, { useState, useEffect, useRef } from "react";
import { Mic, Send, Square, Image as ImageIcon } from "lucide-react";
import { avatarService, conversationService, pipelineService } from "../api/services";
import { API_URL } from "../api/client";
import { AvatarVideo } from "../components/ui/AvatarVideo";
import { Button } from "../components/ui/Button";

export const Dashboard = () => {
  const [avatars, setAvatars] = useState([]);
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [jobStatus, setJobStatus] = useState(null);
  const [currentVideoUrl, setCurrentVideoUrl] = useState(null);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    initDashboard();
  }, []);

  const initDashboard = async () => {
    try {
      const systemAvatars = await avatarService.getSystemAvatars();
      setAvatars(systemAvatars);
      const myAvatars = await avatarService.getMyAvatars();
      const activeAv = myAvatars.find((a) => a.is_active);
      if (activeAv) {
        const matchingSystem = systemAvatars.find((a) => a.name === activeAv.name);
        if (matchingSystem) {
          setSelectedAvatar(matchingSystem);
        }
      } else if (systemAvatars.length > 0) {
        setSelectedAvatar(systemAvatars[0]);
        await avatarService.selectAvatar(systemAvatars[0].name);
      }
      const convList = await conversationService.getList();
      if (convList.length > 0) {
        setConversation(convList[0]);
      } else {
        const newConv = await conversationService.create("My Conversation");
        setConversation(newConv);
      }
    } catch (err) {
      setError("Failed to initialize dashboard");
      console.error(err);
    }
  };

  const pollJobStatus = async (jobId) => {
    try {
      const statusRes = await pipelineService.getStatus(jobId);
      setJobStatus(statusRes.status);
      if (statusRes.status === "done") {
        if (statusRes.video_url) {
          const fullUrl = statusRes.video_url.startsWith("http") 
            ? statusRes.video_url 
            : `${API_URL}${statusRes.video_url}`;
          setCurrentVideoUrl(fullUrl);
        }
      } else if (statusRes.status === "failed") {
        setError(statusRes.error || "Generation failed.");
      } else {
        setTimeout(() => pollJobStatus(jobId), 2000);
      }
    } catch (err) {
      console.error("Failed to poll status:", err);
      setJobStatus("failed");
      setError("Failed to check status.");
    }
  };

  const handleSendText = async () => {
    if (!inputText.trim() || !conversation) return;
    setError(null);
    setJobStatus("pending");
    setCurrentVideoUrl(null);
    try {
      const res = await pipelineService.submitText(conversation.id, inputText);
      setInputText("");
      pollJobStatus(res.job_id);
    } catch (err) {
      setError("Failed to submit text.");
      setJobStatus(null);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());
        setError(null);
        setJobStatus("pending");
        setCurrentVideoUrl(null);
        try {
          const res = await pipelineService.submitVoice(conversation.id, audioBlob);
          pollJobStatus(res.job_id);
        } catch (err) {
          setError("Failed to submit audio.");
          setJobStatus(null);
        }
      };
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Microphone access denied or not available.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleAvatarSelect = async (av) => {
    setSelectedAvatar(av);
    setCurrentVideoUrl(null);
    try {
      await avatarService.selectAvatar(av.name);
    } catch (err) {
      console.error("Failed to select avatar on backend:", err);
      setError("Failed to persist avatar selection.");
    }
  };

  const getAvatarImageUrl = (path) => {
    if (!path) return null;
    return path.startsWith("http") ? path : `${API_URL}${path}`;
  };

  return (
    <div className="flex flex-col lg:flex-row gap-8 h-[calc(100vh-8rem)]">
      <div className="flex-1 flex flex-col items-center justify-center space-y-6">
        <AvatarVideo 
          videoUrl={currentVideoUrl}
          imageUrl={getAvatarImageUrl(selectedAvatar?.image_url)}
          status={jobStatus}
        />
        {error && (
          <div className="text-red-400 bg-red-500/10 border border-red-500/20 p-4 rounded-md w-full max-w-2xl text-center">
            {error}
          </div>
        )}
      </div>

      <div className="w-full lg:w-96 flex flex-col gap-6">
        <div className="glass-panel p-6 rounded-xl flex-1 flex flex-col">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
            <ImageIcon size={16} /> Selected Avatar
          </h2>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {avatars.map((av) => (
              <button
                key={av.name}
                onClick={() => handleAvatarSelect(av)}
                className={`relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                  selectedAvatar?.name === av.name ? "border-white" : "border-transparent opacity-50 hover:opacity-100"
                }`}
              >
                <img src={getAvatarImageUrl(av.image_url)} alt={av.name} className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
          <div className="mt-auto space-y-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-2 flex items-center gap-2">
              <Mic size={16} /> Input
            </h2>
            <div className="relative">
              <textarea
                className="w-full bg-[#1a1a1a] border border-[#333333] rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-white resize-none h-24 text-sm"
                placeholder="Type your message here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={jobStatus === "pending" || jobStatus === "processing"}
              />
              <Button
                size="icon"
                variant="primary"
                className="absolute bottom-2 right-2 w-8 h-8 rounded-md"
                onClick={handleSendText}
                disabled={!inputText.trim() || jobStatus === "pending" || jobStatus === "processing"}
              >
                <Send size={14} />
              </Button>
            </div>
            <div className="flex items-center justify-between text-sm text-gray-400 my-2">
              <hr className="flex-1 border-[#333333]" />
              <span className="px-3">or</span>
              <hr className="flex-1 border-[#333333]" />
            </div>
            <Button
              className={`w-full justify-center gap-2 ${isRecording ? 'bg-red-500 hover:bg-red-600 text-white border-none' : ''}`}
              variant={isRecording ? 'primary' : 'secondary'}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={jobStatus === "pending" || jobStatus === "processing"}
            >
              {isRecording ? <Square size={16} /> : <Mic size={16} />}
              {isRecording ? "Stop Recording" : "Record Audio"}
            </Button>
            {isRecording && (
              <p className="text-center text-red-400 text-xs animate-pulse">Recording...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
