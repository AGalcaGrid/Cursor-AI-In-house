interface SelectOption {
  value: string;
  label: string;
}

interface FormSelectProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export default function FormSelect({
  id,
  label,
  value,
  onChange,
  options,
  error,
  disabled = false,
  required = false,
}: FormSelectProps) {
  return (
    <div className="py-4">
      <label 
        htmlFor={id} 
        className={`block text-sm font-medium mb-2 ${error ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={`
          w-full px-3 py-2 bg-white dark:bg-gray-700 border rounded-lg 
          text-gray-900 dark:text-gray-100
          focus:outline-none focus:ring-2 focus:border-transparent
          transition-colors
          ${error 
            ? 'border-red-300 dark:border-red-600 focus:ring-red-500' 
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-800' : ''}
        `}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
