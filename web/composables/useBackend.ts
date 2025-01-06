import { io, Socket } from "socket.io-client";
import type {
  ChatMessage,
  DataExtracted,
  SearchResult,
  StoryResult,
} from "~/type/ChatMessage.type";

const socket: Socket = io("http://localhost:8000", {
  transports: ["websocket"],
  path: "/socket.io",
});

export const useBackend = () => {
  socket.onAny((event: keyof typeof events, data) => {
    console.log(`Received event ${event}:`, data);
    events[event]?.(data);
  });

  const sendEvent = <T>(eventName: string, payload: any): Promise<T> => {
    return new Promise((resolve, reject) => {
      try {
        socket
          .emit(eventName, payload, (response: T) => {
            console.log(`Received response for ${eventName}:`, response);
            resolve(response);
          })
          .timeout(5000);
      } catch (error) {
        reject(error);
      }
    });
  };
  const methods = {
    sendMessage: async (data: {
      messages: ChatMessage[];
      currentSteps: (DataExtracted | SearchResult | StoryResult)[];
    }): Promise<any> => {
      const response = await sendEvent<any>("message", data);
      return response;
    },
  };
  const events = {} as Record<string, (data: any) => void>;

  const on = {
    message: (callback: (message: ChatMessage) => void) => {
      events.message = callback;
    },
  };

  return {
    ...methods,
    on,
  };
};
