import FileUpload from "@/components/FileUpload";
import ModelSelect from "@/components/ModelSelect";
import Navbar from "@/components/Navbar";

export default function Home() {
  const models: string[] = ["ResNet-18", "Model 2", "Model 3", "Model 4"];
  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <h2 className="text-3xl font-bold text-gray-400 mb-8">Select Model</h2>
        <ModelSelect models={models} />
        <hr className="w-48 h-1 mx-auto my-4 bg-gray-100 border-0 rounded md:my-10 dark:bg-gray-700" />
        <h3 className="text-2xl font-bold text-gray-400 mb-8">Upload Model Parameters</h3>
        <FileUpload expectedFileType="pt" label="Select File (.pt)" />
      </div>
    </main>
  )
}
