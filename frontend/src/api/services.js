import client from "./client";

export const authService = {
  login: async (email, password) => {
    const response = await client.post("/auth/login", { email, password });
    return response.data;
  },
  register: async (email, password, username) => {
    const response = await client.post("/auth/register", { email, password, username });
    return response.data;
  },
  getMe: async () => {
    const response = await client.get("/auth/me");
    return response.data;
  },
};

export const avatarService = {
  getSystemAvatars: async () => {
    const response = await client.get("/avatars/system");
    return response.data;
  },
  selectAvatar: async (system_avatar_name) => {
    const response = await client.post("/avatars/select", { system_avatar_name });
    return response.data;
  },
  getMyAvatars: async () => {
    const response = await client.get("/avatars/me");
    return response.data;
  },
};

export const conversationService = {
  create: async (title) => {
    const response = await client.post("/conversations", { title });
    return response.data;
  },
  getList: async () => {
    const response = await client.get("/conversations");
    return response.data;
  },
  getDetail: async (id) => {
    const response = await client.get(`/conversations/${id}`);
    return response.data;
  },
};

export const pipelineService = {
  submitText: async (conversation_id, text) => {
    const response = await client.post("/pipeline/text", {
      conversation_id,
      text,
      generate_lipsync: true,
    });
    return response.data;
  },
  submitVoice: async (conversation_id, audioBlob) => {
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "recording.webm");
    formData.append("conversation_id", conversation_id);
    formData.append("generate_lipsync", "true");

    const response = await client.post("/pipeline/voice", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
  getStatus: async (job_id) => {
    const response = await client.get(`/pipeline/status/${job_id}`);
    return response.data;
  },
};
