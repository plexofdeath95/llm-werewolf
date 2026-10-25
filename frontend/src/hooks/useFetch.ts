// Minimal async loader: { data, error, loading, reload }.
import { useCallback, useEffect, useState } from 'react'

export function useFetch<T>(load: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | undefined>()
  const [error, setError] = useState<string | undefined>()
  const [loading, setLoading] = useState(true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(load, deps)

  const reload = useCallback(() => {
    setLoading(true)
    run()
      .then((d) => { setData(d); setError(undefined) })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [run])

  useEffect(reload, [reload])
  return { data, error, loading, reload }
}
