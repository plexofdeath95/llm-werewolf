// Create the WebGL2 renderer ourselves, relaxing context attributes until the driver accepts
// one. Some drivers (Firefox + ANGLE: FEATURE_FAILURE_EGL_NO_CONFIG) reject R3F's defaults
// (antialias + alpha + high-performance) but happily create a plainer context.
import { WebGLRenderer } from 'three'

const ATTEMPTS: WebGLContextAttributes[] = [
  { antialias: true, alpha: true, powerPreference: 'high-performance' },
  { antialias: true, alpha: false, powerPreference: 'default' },
  { antialias: false, alpha: false, powerPreference: 'default' },
  { antialias: false, alpha: false, depth: true, stencil: false, powerPreference: 'low-power' },
]

// R3F passes its default props; only the canvas matters here.
export function createRenderer(defaults: { canvas: unknown }): WebGLRenderer {
  const canvas = defaults.canvas as HTMLCanvasElement
  for (const attrs of ATTEMPTS) {
    const context = canvas.getContext('webgl2', attrs)
    if (!context) continue
    console.info('[gl] WebGL2 context created with', attrs)
    return new WebGLRenderer({
      canvas, context, antialias: attrs.antialias, alpha: attrs.alpha,
      powerPreference: attrs.powerPreference,
    })
  }
  throw new Error('No WebGL2 context with any attribute set. Open /webgl-check.html for details.')
}
