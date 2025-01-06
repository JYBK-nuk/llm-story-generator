export interface ChatMessage {
  id: string;
  content: string;
  type: "user" | "bot";
  steps: (DataExtracted | SearchResult | StoryResult)[];
}

export interface DataExtracted {
  type: "extracted";
  data: {
    theme: string;
    genre: string;
    tone: string;
    key_elements: string[];
    language: string;
  };
}

export interface SearchResult {
  type: "searchResult";
  data: {
    title: string;
    url: string;
    description: string;
  }[];
}

export interface StoryResult {
  type: "storyResult";
  data: {
    title: string;
    content: string;
    image: string;
  };
}
