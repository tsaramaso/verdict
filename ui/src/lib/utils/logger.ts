/**
 * Frontend logger utility using loglevel
 * Mirrors backend loguru setup with structured logging
 *
 * Usage:
 *   const log = getLogger('myModule')
 *   log.info('action_name', { key: 'value' })
 *   log.error('error_event', { error: 'details' })
 *
 * Levels: trace, debug, info, warn, error
 * Control via: localStorage.setItem('loglevel', 'info')
 */

import loglevel from 'loglevel';

type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
	[key: string]: unknown;
}

/**
 * Initialize global log level from environment or localStorage
 */
function initializeLogLevel(): void {
	// Check localStorage first (allows runtime override)
	const stored = typeof window !== 'undefined' ? localStorage.getItem('loglevel') : null;

	// Fall back to environment or defaults
	const level = stored || (import.meta.env.MODE === 'production' ? 'info' : 'debug');

	loglevel.setLevel(level as LogLevel);
}

/**
 * Format context object as readable key=value pairs
 */
function formatContext(ctx: LogContext): string {
	const pairs = Object.entries(ctx)
		.map(([k, v]) => {
			if (typeof v === 'object') return `${k}=${JSON.stringify(v)}`;
			return `${k}=${v}`;
		})
		.join(' ');
	return pairs ? ` ${pairs}` : '';
}

/**
 * Get a named logger instance
 */
export function getLogger(module: string) {
	// Initialize on first logger creation
	if (loglevel.getLevel() === loglevel.levels.SILENT) {
		initializeLogLevel();
	}

	const prefix = `[${module}]`;

	return {
		trace: (event: string, ctx?: LogContext) => {
			loglevel.trace(`${prefix} ${event}${formatContext(ctx || {})}`);
		},
		debug: (event: string, ctx?: LogContext) => {
			loglevel.debug(`${prefix} ${event}${formatContext(ctx || {})}`);
		},
		info: (event: string, ctx?: LogContext) => {
			loglevel.info(`${prefix} ${event}${formatContext(ctx || {})}`);
		},
		warn: (event: string, ctx?: LogContext) => {
			loglevel.warn(`${prefix} ${event}${formatContext(ctx || {})}`);
		},
		error: (event: string, ctx?: LogContext) => {
			loglevel.error(`${prefix} ${event}${formatContext(ctx || {})}`);
		}
	};
}

/**
 * Set global log level at runtime
 * Useful for debugging: setLogLevel('debug')
 */
export function setLogLevel(level: LogLevel): void {
	loglevel.setLevel(level);
	if (typeof window !== 'undefined') {
		localStorage.setItem('loglevel', level);
	}
}

/**
 * Get current log level
 */
export function getLogLevel(): string {
	return loglevel.getLevel().toString();
}
