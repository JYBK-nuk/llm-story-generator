import { io, Socket } from "socket.io-client";
import type { ChatMessage } from "~/type/ChatMessage.type";
const socket: Socket = io("http://localhost:8000", {
  transports: ["websocket"],
  path: "/socket.io",
});

export const useBackend = () => {
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
    sendMessage: async (messages: ChatMessage[]): Promise<any> => {
      const response = await sendEvent<any>("message", messages);
      return response;
    },

    sendName: async (name: string): Promise<any> => {
      const response = await sendEvent<any>("name", { name });
      return response;
    },
  };

  return {
    ...methods,
  };
};
