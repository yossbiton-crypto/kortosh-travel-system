import { PRIORITIES, STATUSES } from '../constants.js';

export const PriorityBadge = ({ value }) => <span className={`badge p${value}`}>{PRIORITIES[value]}</span>;
export const StatusBadge = ({ value }) => <span className={`badge s-${value}`}>{STATUSES[value] || value}</span>;
