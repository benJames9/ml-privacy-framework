import ModelSelect from "../components/ModelSelect";

export default function Home() {
  const models: string[] = ["ResNet-18", "Model 2", "Model 3", "Model 4"];
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gradient-to-r from-black to-blue-950">
      <ModelSelect models={models} />
    </main>
  )
}
