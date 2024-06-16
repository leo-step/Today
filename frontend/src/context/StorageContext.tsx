import React, { createContext, useContext, ReactNode } from "react";

type Storage = {
  getLocalStorage: (key: string) => string | null;
  getLocalStorageDefault: (key: string, fallback: string) => string;
  setLocalStorage: (key: string, data: string) => void;
};

const storageContext: Storage = {
  getLocalStorage: (key: string) => {
    return window.localStorage.getItem(key);
  },
  getLocalStorageDefault: (key: string, fallback: string) => {
    return window.localStorage.getItem(key) || fallback;
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
