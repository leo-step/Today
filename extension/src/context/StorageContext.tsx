import React, { createContext, useContext, ReactNode } from "react";

export enum StorageKeys {
  UUID = "uuid",
  DATA = "data",
  WIDGET = "campusWidget",
  NAME = "name",
  DHALL = "dhall",
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

const cleanLocalStorage = () => {
  const allKeys = Object.keys(localStorage);
  const storageKeysArray = Object.values(StorageKeys) as string[];

  allKeys.forEach((key) => {
    if (!storageKeysArray.includes(key)) {
      localStorage.removeItem(key);
    }
  });
};

const storageContext: Storage = {
  getLocalStorage: (key: StorageKeys) => {
    cleanLocalStorage()
    return window.localStorage.getItem(key);
  },
  getLocalStorageDefault: (
    key: StorageKeys,
    fallback: string,
    // MUST include array for all widgets, otherwise breaking on extension update
    validResults?: string[]
  ) => {
    cleanLocalStorage()
    let result = window.localStorage.getItem(key) || fallback;
    if (validResults && !validResults.includes(result)) {
      result = validResults[0];
    }
    return result;
  },
  setLocalStorage: (key: StorageKeys, data: string) => {
    cleanLocalStorage()
    window.localStorage.setItem(key, data);
  },
  getLocalStorageObject: () => {
    cleanLocalStorage();
  
    const localStorageObject = Object.fromEntries(
      Object.values(StorageKeys).map((key) => {
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
  
    delete localStorageObject[StorageKeys.DATA];
    delete localStorageObject[StorageKeys.UUID];
  
    return localStorageObject;
  }
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
