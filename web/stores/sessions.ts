import { defineStore } from "pinia";
import type { ChatMessage } from "~/type/ChatMessage.type";

export const useSessionsStore = defineStore("SessionsStore", {
  state: () => ({
    _sessions: [] as {
      sid: string;
      created_at: string;
      updated_at: string;
      messages: ChatMessage[];
    }[],
  }),

  actions: {
    init() {
      this._sessions = this._sessions.filter((s) => s.messages.length > 0);
    },
    cleanSessions() {
      this._sessions = [];
    },
    addSession() {
      const uuid = crypto.randomUUID();
      this._sessions.push({
        sid: uuid,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: [],
      });
      return uuid;
    },
    updateSession(sid: string, messages: ChatMessage[]) {
      const session = this._sessions.find((s) => s.sid === sid);
      if (session) {
        session.messages = messages;
      }
    },
    getSession(sid: string) {
      return this._sessions.find((s) => s.sid === sid);
    },
  },
  getters: {
    sessions: (state) =>
      state._sessions.map((s) => {
        return {
          sid: s.sid,
          title: s.messages.at(-1)?.content || "無內容",
          created_at: s.created_at,
          updated_at: s.updated_at,
        };
      }),
  },
  persist: {
    key: "sessions",
    storage: piniaPluginPersistedstate.localStorage(),
  },
});
