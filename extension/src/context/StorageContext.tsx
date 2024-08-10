import React, { createContext, useContext, ReactNode } from "react";

export enum StorageKeys {
  UUID = "uuid",
  DATA = "data",
  WIDGET = "campusWidget",
  NAME = "name",
  DHALL = "dhall",
  CLUB = "club",
}

type Storage = {
  getLocalStorage: (key: StorageKeys) => string | null;
  getLocalStorageDefault: (
    key: StorageKeys,
    fallback: string,
    validSettings?: string[]
  ) => string;
  setLocalStorage: (key: StorageKeys, data: string) => void;
  getLocalStorageObject: () => any;
};

const storageContext: Storage = {
  getLocalStorage: (key: StorageKeys) => {
    return window.localStorage.getItem(key);
  },
  getLocalStorageDefault: (
    key: StorageKeys,
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
  setLocalStorage: (key: StorageKeys, data: string) => {
    window.localStorage.setItem(key, data);
  },
  getLocalStorageObject: () => {
    const localStorageObject = Object.fromEntries(
      Object.keys(localStorage).map((key) => {
        const value = localStorage.getItem(key);
        if (!value) {
          return [key, null];
        }
        try {
          return [key, JSON.parse(value)];
        } catch (e) {
          return [key, value];
        }
      })
    );
    delete localStorageObject.data;
    delete localStorageObject.uuid;
    return localStorageObject;
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
