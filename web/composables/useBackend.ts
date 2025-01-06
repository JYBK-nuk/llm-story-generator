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
      currentStoryBoard: {
        dataExtracted: DataExtracted | null;
        storyResult: StoryResult | null;
        searchResult: SearchResult | null;
      };
    }): Promise<any> => {
      const data_ = {
        messages: data.messages,
        currentStoryBoard: {
          data_extracted: data.currentStoryBoard.dataExtracted,
          story_result: data.currentStoryBoard.storyResult,
          search_result: data.currentStoryBoard.searchResult,
        },
      };
      const response = await sendEvent<any>("message", data_);
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
