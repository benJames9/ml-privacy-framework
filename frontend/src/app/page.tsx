"use client";
import Navbar from "@/components/Navbar";
import StartAttackCard from "@/components/StartAttackCard";
import ViewAttackCard from "@/components/ViewAttackCard";

const HomePage: React.FC = () => {
  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen bg-gradient-to-r from-black to-blue-950">
        <div className="py-8 px-4 mx-auto max-w-screen-xl lg:py-10">
          <div className="grid md:grid-cols-2 gap-2">
            <StartAttackCard />
            <ViewAttackCard />
          </div>
        </div>
      </div>
    </main>
  );
}

export default HomePage;