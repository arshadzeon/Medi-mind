"use client";
import { useRef, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei'
import * as THREE from 'three'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

function AnimatedSphere() {
  const sphereRef = useRef<THREE.Mesh>(null!)
  const { camera } = useThree()
  
  useEffect(() => {
    // Initial animation
    gsap.from(sphereRef.current.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 1.5,
      ease: "elastic.out(1, 0.3)"
    })

    // Scroll animation
    gsap.to(sphereRef.current.position, {
      y: -1,
      scrollTrigger: {
        trigger: "canvas",
        start: "top top",
        end: "bottom center",
        scrub: 1,
      }
    })
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    sphereRef.current.rotation.x = t * 0.1
    sphereRef.current.rotation.y = t * 0.15
  })

  return (
    <Sphere ref={sphereRef} args={[1, 100, 100]}>
      <MeshDistortMaterial
        color="#4F46E5"
        attach="material"
        distort={0.5}
        speed={2}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  )
}

function FloatingParticles() {
  const particlesRef = useRef<THREE.Points>(null!)
  const count = 2000
  const positions = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    const i3 = i * 3
    positions[i3] = (Math.random() - 0.5) * 10
    positions[i3 + 1] = (Math.random() - 0.5) * 10
    positions[i3 + 2] = (Math.random() - 0.5) * 10
  }

  useEffect(() => {
    // Particles fade in
    gsap.from(particlesRef.current.material, {
      opacity: 0,
      duration: 2,
      ease: "power2.out"
    })

    // Scroll animation
    gsap.to(particlesRef.current.rotation, {
      y: Math.PI * 2,
      scrollTrigger: {
        trigger: "canvas",
        start: "top top",
        end: "bottom bottom",
        scrub: 2,
      }
    })
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    particlesRef.current.rotation.x = t * 0.03
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#8B5CF6"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  )
}

export default function ThreeHero() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Camera scroll animation
    const canvas = containerRef.current?.querySelector('canvas')
    if (canvas) {
      gsap.to(canvas, {
        scale: 0.8,
        scrollTrigger: {
          trigger: canvas,
          start: "top top",
          end: "bottom center",
          scrub: 1,
        }
      })
    }
  }, [])

  return (
    <div ref={containerRef} className="absolute inset-0 -z-10">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 75 }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <AnimatedSphere />
        <FloatingParticles />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.5}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 2}
        />
      </Canvas>
    </div>
  )
} 