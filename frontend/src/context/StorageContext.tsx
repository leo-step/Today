import React, { createContext, useContext, ReactNode } from "react";

type Storage = {
  getLocalStorage: (key: string) => string | null;
  getLocalStorageDefault: (
    key: string,
    fallback: string,
    validSettings?: string[]
  ) => string;
  setLocalStorage: (key: string, data: string) => void;
};

const storageContext: Storage = {
  getLocalStorage: (key: string) => {
    return window.localStorage.getItem(key);
  },
  getLocalStorageDefault: (
    key: string,
    fallback: string,
    // MUST include array for all widgets, otherwise breaking on extension update
    validResults?: string[]
  ) => {
    let result = window.localStorage.getItem(key) || fallback;
    if (validResults && !validResults.includes(result)) {
      result = validResults[0];
    }
    return result;
  },
  setLocalStorage: (key: string, data: string) => {
    window.localStorage.setItem(key, data);
  },
};

const StorageContext = createContext<Storage>(storageContext);

const StorageProvider = ({ children }: { children: ReactNode }) => {
  return (
    <StorageContext.Provider value={storageContext}>
      {children}
    </StorageContext.Provider>
  );
};

const useStorage = () => {
  return useContext(StorageContext);
};

export { StorageProvider, useStorage };
