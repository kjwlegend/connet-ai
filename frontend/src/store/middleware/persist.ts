import { PersistOptions, subscribeWithSelector, persist } from 'zustand/middleware'
import { StateCreator } from 'zustand'
import { StorageUtil } from '@/lib/utils/storage'

interface PersistStorage {
  getItem: (name: string) => string | null | Promise<string | null>
  setItem: (name: string, value: string) => void | Promise<void>
  removeItem: (name: string) => void | Promise<void>
}

const createCustomStorage = (): PersistStorage => ({
  getItem: (name: string) => {
    const value = StorageUtil.getItem<string>(name)
    return value
  },
  setItem: (name: string, value: string) => {
    StorageUtil.setItem(name, value)
  },
  removeItem: (name: string) => {
    StorageUtil.removeItem(name)
  },
})

export const createPersistOptions = <T>(
  name: string,
  partialize?: (state: T) => Partial<T>
): PersistOptions<T> => ({
  name,
  storage: createCustomStorage(),
  partialize,
})

export { persist, subscribeWithSelector }