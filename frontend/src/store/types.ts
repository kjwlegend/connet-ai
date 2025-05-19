// src/store/types.ts
import { AuthSlice } from './slices/authSlice'
import { SettingsState, SettingsActions } from './slices/settingsSlice'
// If you have other slices, import their types here. For example:
// import { CartSlice } from './slices/cartSlice';

/**
 * Represents the complete state of the application store.
 * It's a combination of all individual slice states and actions.
 */
export type StoreState = AuthSlice & SettingsState & SettingsActions
// & CartSlice; // Add other slice types here if they exist
